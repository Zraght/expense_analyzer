"""
Test validators module.

This module contains unit tests for data validation utilities.
"""

import pytest
import pandas as pd
from utils.validators import (
    DataValidationError,
    validate_dataframe_not_empty,
    validate_required_columns,
    validate_column_types,
    validate_numeric_range,
    validate_no_nulls,
    check_data_quality
)


class TestValidateDataframeNotEmpty:
    """Test suite for validate_dataframe_not_empty function."""
    
    def test_valid_dataframe(self):
        """Test that valid DataFrame passes validation."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        validate_dataframe_not_empty(df)  # Should not raise
    
    def test_none_dataframe(self):
        """Test that None raises DataValidationError."""
        with pytest.raises(DataValidationError):
            validate_dataframe_not_empty(None)
    
    def test_empty_dataframe(self):
        """Test that empty DataFrame raises DataValidationError."""
        df = pd.DataFrame()
        with pytest.raises(DataValidationError):
            validate_dataframe_not_empty(df)


class TestValidateRequiredColumns:
    """Test suite for validate_required_columns function."""
    
    def test_all_columns_present(self):
        """Test that DataFrame with all required columns passes."""
        df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3]})
        validate_required_columns(df, ['A', 'B', 'C'])  # Should not raise
    
    def test_missing_columns(self):
        """Test that missing columns raise DataValidationError."""
        df = pd.DataFrame({'A': [1], 'B': [2]})
        with pytest.raises(DataValidationError):
            validate_required_columns(df, ['A', 'B', 'C'])
    
    def test_subset_of_columns(self):
        """Test validation with subset of columns."""
        df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3], 'D': [4]})
        validate_required_columns(df, ['A', 'C'])  # Should not raise


class TestValidateColumnTypes:
    """Test suite for validate_column_types function."""
    
    def test_numeric_type_validation(self):
        """Test numeric type validation."""
        df = pd.DataFrame({'Amount': [1.5, 2.5, 3.5]})
        validate_column_types(df, {'Amount': 'numeric'})  # Should not raise
    
    def test_datetime_type_validation(self):
        """Test datetime type validation."""
        df = pd.DataFrame({'Date': pd.to_datetime(['2024-01-01', '2024-01-02'])})
        validate_column_types(df, {'Date': 'datetime'})  # Should not raise
    
    def test_invalid_type(self):
        """Test that invalid type raises DataValidationError."""
        df = pd.DataFrame({'Amount': ['a', 'b', 'c']})
        with pytest.raises(DataValidationError):
            validate_column_types(df, {'Amount': 'numeric'})


class TestValidateNumericRange:
    """Test suite for validate_numeric_range function."""
    
    def test_values_in_range(self):
        """Test that values in range pass validation."""
        df = pd.DataFrame({'Amount': [10, 20, 30]})
        validate_numeric_range(df, 'Amount', min_value=0, max_value=100)  # Should not raise
    
    def test_negative_values_not_allowed(self):
        """Test that negative values raise error when not allowed."""
        df = pd.DataFrame({'Amount': [-10, 20, 30]})
        with pytest.raises(DataValidationError):
            validate_numeric_range(df, 'Amount', allow_negative=False)
    
    def test_values_below_minimum(self):
        """Test that values below minimum raise error."""
        df = pd.DataFrame({'Amount': [5, 10, 15]})
        with pytest.raises(DataValidationError):
            validate_numeric_range(df, 'Amount', min_value=10)
    
    def test_values_above_maximum(self):
        """Test that values above maximum raise error."""
        df = pd.DataFrame({'Amount': [50, 100, 150]})
        with pytest.raises(DataValidationError):
            validate_numeric_range(df, 'Amount', max_value=100)


class TestValidateNoNulls:
    """Test suite for validate_no_nulls function."""
    
    def test_no_nulls(self):
        """Test that DataFrame with no nulls passes."""
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        validate_no_nulls(df, ['A', 'B'])  # Should not raise
    
    def test_nulls_present(self):
        """Test that DataFrame with nulls raises error."""
        df = pd.DataFrame({'A': [1, None, 3], 'B': [4, 5, 6]})
        with pytest.raises(DataValidationError):
            validate_no_nulls(df, ['A'])
    
    def test_validate_all_columns(self):
        """Test validating all columns when none specified."""
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, None, 6]})
        with pytest.raises(DataValidationError):
            validate_no_nulls(df)  # Check all columns


class TestCheckDataQuality:
    """Test suite for check_data_quality function."""
    
    def test_remove_null_rows(self):
        """Test removing rows with null values."""
        df = pd.DataFrame({'A': [1, None, 3], 'B': [4, 5, None]})
        cleaned = check_data_quality(df, remove_nulls=True)
        assert len(cleaned) == 1  # Only first row has no nulls
    
    def test_remove_duplicates(self):
        """Test removing duplicate rows."""
        df = pd.DataFrame({'A': [1, 1, 2], 'B': [3, 3, 4]})
        cleaned = check_data_quality(df, remove_duplicates=True)
        assert len(cleaned) == 2  # One duplicate removed
    
    def test_no_cleaning_needed(self):
        """Test DataFrame that needs no cleaning."""
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        cleaned = check_data_quality(df, remove_nulls=True, remove_duplicates=True)
        assert len(cleaned) == 3  # No rows removed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
