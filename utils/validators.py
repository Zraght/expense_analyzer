"""
Data validation utilities.

This module provides validation functions for data quality checks.
"""

import logging
import pandas as pd
from typing import List, Optional

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


def validate_dataframe_not_empty(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Validate that a DataFrame is not None or empty.
    
    Args:
        df: DataFrame to validate.
        name: Name of the DataFrame for error messages.
        
    Raises:
        DataValidationError: If DataFrame is None or empty.
        
    Example:
        >>> validate_dataframe_not_empty(expenses_df, "Expenses")
    """
    if df is None:
        error_msg = f"{name} is None"
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    if df.empty:
        error_msg = f"{name} is empty - no data to process"
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    logger.debug(f"{name} validation passed: {len(df)} rows")


def validate_required_columns(
    df: pd.DataFrame, 
    required_columns: List[str],
    name: str = "DataFrame"
) -> None:
    """
    Validate that a DataFrame contains all required columns.
    
    Args:
        df: DataFrame to validate.
        required_columns: List of required column names.
        name: Name of the DataFrame for error messages.
        
    Raises:
        DataValidationError: If any required columns are missing.
        
    Example:
        >>> validate_required_columns(df, ['Date', 'Amount', 'Category'])
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        error_msg = (
            f"{name} is missing required columns: {', '.join(missing_columns)}\n"
            f"Found columns: {', '.join(df.columns)}\n"
            f"Required columns: {', '.join(required_columns)}"
        )
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    logger.debug(f"{name} has all required columns: {', '.join(required_columns)}")


def validate_column_types(
    df: pd.DataFrame,
    column_types: dict,
    name: str = "DataFrame"
) -> None:
    """
    Validate that DataFrame columns have expected types.
    
    Args:
        df: DataFrame to validate.
        column_types: Dictionary mapping column names to expected types.
        name: Name of the DataFrame for error messages.
        
    Raises:
        DataValidationError: If column types don't match expectations.
        
    Example:
        >>> validate_column_types(df, {'Amount': 'float64', 'Date': 'datetime64'})
    """
    type_errors = []
    
    for column, expected_type in column_types.items():
        if column not in df.columns:
            continue
        
        actual_type = str(df[column].dtype)
        
        # Handle generic type matching
        if expected_type in ['numeric', 'number']:
            if not pd.api.types.is_numeric_dtype(df[column]):
                type_errors.append(
                    f"Column '{column}' should be numeric, got {actual_type}"
                )
        elif expected_type == 'datetime':
            if not pd.api.types.is_datetime64_any_dtype(df[column]):
                type_errors.append(
                    f"Column '{column}' should be datetime, got {actual_type}"
                )
        elif expected_type not in actual_type:
            type_errors.append(
                f"Column '{column}' expected {expected_type}, got {actual_type}"
            )
    
    if type_errors:
        error_msg = f"{name} column type validation failed:\n" + "\n".join(type_errors)
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    logger.debug(f"{name} column types validated successfully")


def validate_numeric_range(
    df: pd.DataFrame,
    column: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_negative: bool = False
) -> None:
    """
    Validate that numeric values in a column are within acceptable range.
    
    Args:
        df: DataFrame containing the column.
        column: Name of the column to validate.
        min_value: Minimum acceptable value (inclusive).
        max_value: Maximum acceptable value (inclusive).
        allow_negative: Whether to allow negative values.
        
    Raises:
        DataValidationError: If values are out of range.
        
    Example:
        >>> validate_numeric_range(df, 'Amount', min_value=0, max_value=10000)
    """
    if column not in df.columns:
        return
    
    errors = []
    
    # Check for negative values if not allowed
    if not allow_negative:
        negative_count = (df[column] < 0).sum()
        if negative_count > 0:
            errors.append(f"Found {negative_count} negative values in '{column}'")
    
    # Check minimum value
    if min_value is not None:
        below_min = (df[column] < min_value).sum()
        if below_min > 0:
            errors.append(
                f"Found {below_min} values in '{column}' below minimum {min_value}"
            )
    
    # Check maximum value
    if max_value is not None:
        above_max = (df[column] > max_value).sum()
        if above_max > 0:
            errors.append(
                f"Found {above_max} values in '{column}' above maximum {max_value}"
            )
    
    if errors:
        error_msg = f"Numeric range validation failed for '{column}':\n" + "\n".join(errors)
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    logger.debug(f"Column '{column}' numeric range validated successfully")


def validate_no_nulls(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    name: str = "DataFrame"
) -> None:
    """
    Validate that specified columns contain no null values.
    
    Args:
        df: DataFrame to validate.
        columns: List of column names to check. If None, checks all columns.
        name: Name of the DataFrame for error messages.
        
    Raises:
        DataValidationError: If null values are found.
        
    Example:
        >>> validate_no_nulls(df, ['Date', 'Amount', 'Category'])
    """
    if columns is None:
        columns = df.columns.tolist()
    
    null_counts = {}
    for col in columns:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                null_counts[col] = null_count
    
    if null_counts:
        error_details = [f"'{col}': {count}" for col, count in null_counts.items()]
        error_msg = (
            f"{name} contains null values:\n" + 
            "\n".join(error_details)
        )
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    logger.debug(f"{name} has no null values in required columns")


def check_data_quality(
    df: pd.DataFrame,
    remove_nulls: bool = True,
    remove_duplicates: bool = False
) -> pd.DataFrame:
    """
    Perform basic data quality checks and cleanup.
    
    Args:
        df: DataFrame to check and clean.
        remove_nulls: Whether to remove rows with null values.
        remove_duplicates: Whether to remove duplicate rows.
        
    Returns:
        Cleaned DataFrame.
        
    Example:
        >>> cleaned_df = check_data_quality(df, remove_nulls=True)
    """
    original_rows = len(df)
    df_cleaned = df.copy()
    
    # Remove null values
    if remove_nulls:
        null_rows = df_cleaned.isna().any(axis=1).sum()
        if null_rows > 0:
            df_cleaned = df_cleaned.dropna()
            logger.info(f"Removed {null_rows} rows with null values")
    
    # Remove duplicates
    if remove_duplicates:
        duplicate_rows = df_cleaned.duplicated().sum()
        if duplicate_rows > 0:
            df_cleaned = df_cleaned.drop_duplicates()
            logger.info(f"Removed {duplicate_rows} duplicate rows")
    
    rows_removed = original_rows - len(df_cleaned)
    if rows_removed > 0:
        logger.info(
            f"Data quality check complete: {rows_removed} rows removed, "
            f"{len(df_cleaned)} rows remaining"
        )
    
    return df_cleaned
