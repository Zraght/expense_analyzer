"""
Test reading module.

This module contains unit tests for expense data reading functionality.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from modules.reading import read_expenses_csv, get_data_summary


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample expense data."""
    csv_content = """Date,Category,Amount,Description
2024-01-15,Food,250.50,Weekly groceries
2024-01-18,Transport,45.00,Gas
2024-01-20,Entertainment,120.00,Movies and dinner
2024-01-22,Health,300.00,Doctor visit
2024-02-01,Services,850.00,Monthly rent
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def invalid_csv_file():
    """Create a temporary CSV file with invalid data."""
    csv_content = """Date,Category,Amount,Description
invalid_date,Food,250.50,Groceries
2024-01-18,Transport,invalid_amount,Gas
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    yield temp_path
    
    Path(temp_path).unlink()


@pytest.fixture
def empty_csv_file():
    """Create an empty CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Date,Category,Amount,Description\n")
        temp_path = f.name
    
    yield temp_path
    
    Path(temp_path).unlink()


class TestReadExpensesCsv:
    """Test suite for read_expenses_csv function."""
    
    def test_read_valid_csv(self, sample_csv_file):
        """Test reading a valid CSV file."""
        df = read_expenses_csv(sample_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == ['Date', 'Category', 'Amount', 'Description']
        assert pd.api.types.is_datetime64_any_dtype(df['Date'])
        assert pd.api.types.is_numeric_dtype(df['Amount'])
    
    def test_read_nonexistent_file(self):
        """Test that reading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_expenses_csv('nonexistent_file.csv')
    
    def test_read_invalid_data(self, invalid_csv_file):
        """Test reading CSV with invalid data."""
        df = read_expenses_csv(invalid_csv_file)
        
        # Invalid rows should be removed
        assert len(df) == 0  # All rows have invalid data
    
    def test_read_empty_file(self, empty_csv_file):
        """Test reading an empty CSV file."""
        with pytest.raises(ValueError):
            read_expenses_csv(empty_csv_file)
    
    def test_missing_required_columns(self):
        """Test that missing required columns raises ValueError."""
        csv_content = """Date,Amount
2024-01-15,250.50
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                read_expenses_csv(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_data_sorting(self, sample_csv_file):
        """Test that data is sorted by date."""
        df = read_expenses_csv(sample_csv_file)
        
        # Check if dates are in ascending order
        assert df['Date'].is_monotonic_increasing


class TestGetDataSummary:
    """Test suite for get_data_summary function."""
    
    def test_summary_structure(self, sample_csv_file):
        """Test that summary has correct structure."""
        df = read_expenses_csv(sample_csv_file)
        summary = get_data_summary(df)
        
        assert 'total_records' in summary
        assert 'date_range' in summary
        assert 'unique_categories' in summary
        assert 'categories' in summary
        assert 'total_amount' in summary
        assert 'average_amount' in summary
    
    def test_summary_values(self, sample_csv_file):
        """Test that summary contains correct values."""
        df = read_expenses_csv(sample_csv_file)
        summary = get_data_summary(df)
        
        assert summary['total_records'] == 5
        assert summary['unique_categories'] == 5
        assert isinstance(summary['categories'], list)
        assert summary['total_amount'] == df['Amount'].sum()
    
    def test_empty_dataframe_raises_error(self):
        """Test that empty DataFrame raises error."""
        from utils.validators import DataValidationError
        
        df = pd.DataFrame()
        with pytest.raises(DataValidationError):
            get_data_summary(df)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
